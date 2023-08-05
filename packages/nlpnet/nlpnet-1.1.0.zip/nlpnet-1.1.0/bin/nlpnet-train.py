#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to train a neural networks for NLP tagging tasks.

Author: Erick Rocha Fonseca
"""

import logging
import numpy as np

import nlpnet.config as config
import nlpnet.read_data as read_data
import nlpnet.utils as utils
import nlpnet.taggers as taggers
import nlpnet.metadata as metadata
import nlpnet.srl as srl
import nlpnet.pos as pos
import nlpnet.arguments as arguments
import nlpnet.reader as reader
import nlpnet.attributes as attributes
from nlpnet.network import Network, ConvolutionalNetwork, LanguageModel


############################
### FUNCTION DEFINITIONS ###
############################

def create_reader(args):
    """
    Creates and returns a TextReader object according to the task at hand.
    """
    logger.info("Reading text...")
    if args.task == 'pos':
        text_reader = pos.pos_reader.POSReader(filename=args.gold)
    
    elif args.task == 'lm':
        text_reader = reader.TextReader(filename=args.gold)

    elif args.task.startswith('srl'):
        text_reader = srl.srl_reader.SRLReader(filename=args.gold, only_boundaries=args.identify, 
                                               only_classify=args.classify,
                                               only_predicates=args.predicates)
    
        if args.semi:
            # load data for semi supervised learning
            data = read_data.read_plain_srl(args.semi)
            text_reader.extend(data)    
    
        if args.identify:
            # only identify arguments
            text_reader.convert_tags('iobes', only_boundaries=True)
            
        elif not args.classify and not args.predicates:
            # this is SRL as one step, we use IOB
            text_reader.convert_tags('iob', update_tag_dict=False)
    
    else:
        raise ValueError("Unknown task: %s" % args.task)
    
    return text_reader
    

def create_network(args, text_reader, feature_tables, md=None):
    """Creates and returns the neural network according to the task at hand."""
    logger = logging.getLogger("Logger")
    
    if args.task.startswith('srl') and args.task != 'srl_predicates':
        num_tags = len(text_reader.tag_dict)
        distance_tables = utils.set_distance_features(args.max_dist, args.target_features,
                                                      args.pred_features)
        nn = ConvolutionalNetwork.create_new(feature_tables, distance_tables[0], 
                                             distance_tables[1], args.window, 
                                             args.convolution, args.hidden, num_tags)
        padding_left = text_reader.converter.get_padding_left(False)
        padding_right = text_reader.converter.get_padding_right(False)
        if args.identify:
            logger.info("Loading initial transition scores table for argument identification")
            transitions = srl.train_srl.init_transitions_simplified(text_reader.tag_dict)
            nn.transitions = transitions
            nn.learning_rate_trans = args.learning_rate_transitions
            
        elif not args.classify:
            logger.info("Loading initial IOB transition scores table")
            transitions = srl.train_srl.init_transitions(text_reader.tag_dict, 'iob')
            nn.transitions = transitions
            nn.learning_rate_trans = args.learning_rate_transitions
    
    elif args.task == 'lm':
        nn = LanguageModel.create_new(feature_tables, args.window, args.hidden)
        padding_left = text_reader.converter.get_padding_left(tokens_as_string=True)
        padding_right = text_reader.converter.get_padding_right(tokens_as_string=True)
        
    else:
        num_tags = len(text_reader.tag_dict)
        nn = Network.create_new(feature_tables, args.window, args.hidden, num_tags)
        if args.learning_rate_transitions > 0:
            transitions = np.zeros((num_tags + 1, num_tags), np.float)
            nn.transitions = transitions
            nn.learning_rate_trans = args.learning_rate_transitions

        padding_left = text_reader.converter.get_padding_left(args.task == 'pos')
        padding_right = text_reader.converter.get_padding_right(args.task == 'pos')
    
    nn.padding_left = np.array(padding_left)
    nn.padding_right = np.array(padding_right)
    nn.learning_rate = args.learning_rate
    nn.learning_rate_features = args.learning_rate_features
    
    if args.task == 'lm':
        layer_sizes = (nn.input_size, nn.hidden_size, 1)
    elif args.convolution > 0 and args.hidden > 0:
        layer_sizes = (nn.input_size, nn.hidden_size, nn.hidden2_size, nn.output_size)
    else:
        layer_sizes = (nn.input_size, nn.hidden_size, nn.output_size)
    
    logger.info("Created new network with the following layer sizes: %s"
                % ', '.join(str(x) for x in layer_sizes))
    
    return nn
        
def save_features(nn, md):
    """
    Receives a sequence of feature tables and saves each one in the appropriate file.
    
    :param nn: the neural network
    :param md: a Metadata object describing the network
    """
    def save_affix_features(affix, iter_tables):
        """
        Helper function for both suffixes and affixes.
        affix should be either 'suffix' or 'affix'
        """
        # there can be an arbitrary number of tables, one for each length
        affix_features = []
        codes = getattr(attributes.Affix, '%s_codes' % affix)
        num_sizes = len(codes)
        for _ in range(num_sizes):
            affix_features.append(iter_tables.next())
        
        filename_key = getattr(md, '%s_features' % affix)
        filename = config.FILES[filename_key]
        utils.save_features_to_file(affix_features, filename)
        
    # type features
    utils.save_features_to_file(nn.feature_tables[0], config.FILES[md.type_features])
    
    # other features - the order is important!
    iter_tables = iter(nn.feature_tables[1:])
    if md.use_caps: utils.save_features_to_file(iter_tables.next(), config.FILES[md.caps_features])
    if md.use_prefix:
        save_affix_features('prefix', iter_tables)
    if md.use_suffix:
        save_affix_features('suffix', iter_tables)
    if md.use_pos: utils.save_features_to_file(iter_tables.next(), config.FILES[md.pos_features])
    if md.use_chunk: utils.save_features_to_file(iter_tables.next(), config.FILES[md.chunk_features])
    
def load_network_train(args, md):
    """Loads and returns a neural network with all the necessary data."""
    nn = taggers.load_network(md)
    
    logger.info("Loaded network with following parameters:")
    logger.info(nn.description())
    
    nn.learning_rate = args.learning_rate
    nn.learning_rate_features = args.learning_rate_features
    if md.task != 'lm':
        nn.learning_rate_trans = args.learning_rate_transitions
    
    return nn

def train(reader, args):
    """Trains a neural network for the selected task."""
    intervals = max(args.iterations / 200, 1)
    np.seterr(over='raise')
    
    if args.task.startswith('srl') and args.task != 'srl_predicates':
        arg_limits = None if args.task != 'srl_classify' else text_reader.arg_limits
        
        nn.train(text_reader.sentences, text_reader.predicates, text_reader.tags, 
                 args.iterations, intervals, args.accuracy, arg_limits)
    elif args.task == 'lm':
        nn.train(text_reader.sentences, args.iterations, intervals)
    else:
        nn.train(text_reader.sentences, text_reader.tags, 
                 args.iterations, intervals, args.accuracy)



if __name__ == '__main__':
    args = arguments.get_args()
    args = arguments.check_arguments(args)

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    utils.set_logger(logging_level)
    logger = logging.getLogger("Logger")

    config.set_data_dir(args.data)
    text_reader = create_reader(args)
    
    use_caps = args.caps is not None
    use_suffix = args.suffix is not None
    use_prefix = args.prefix is not None
    use_pos = args.pos is not None
    use_chunk = args.chunk is not None
    use_lemma = args.use_lemma
    
    if not args.load_network:
        # if we are about to create a new network, create the metadata too
        md = metadata.Metadata(args.task, use_caps, use_suffix, use_prefix, 
                               use_pos, use_chunk, use_lemma)
        md.save_to_file()
    else:
        md = metadata.Metadata.load_from_file(args.task)
    
    text_reader.create_converter(md)
    text_reader.codify_sentences()
    
    if args.load_network or args.semi:
        logger.info("Loading provided network...")
        nn = load_network_train(args, md)
    else:
        logger.info('Creating new network...')
        feature_tables = utils.create_feature_tables(args, md, text_reader)
        nn = create_network(args, text_reader, feature_tables, md)
    
    logger.info("Starting training with %d sentences" % len(text_reader.sentences))
    train(text_reader, args)
    
    logger.info("Saving trained models...")
    save_features(nn, md)
    
    nn_file = config.FILES[md.network]
    nn.save(nn_file)
    logger.info("Saved network to %s" % nn_file)
    
