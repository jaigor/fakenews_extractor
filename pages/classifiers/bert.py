import os

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from official.nlp import optimization  # to create AdamW optimizer

tf.get_logger().setLevel('ERROR')

map_name_to_handle = {
    'bert_en_uncased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4',
    'bert_en_cased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_cased_L-12_H-768_A-12/4',
    'bert_en_wwm_cased_L-24_H-1024_A-16':
        'https://tfhub.dev/tensorflow/bert_en_wwm_cased_L-24_H-1024_A-16/4',
    'bert_multi_cased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_multi_cased_L-12_H-768_A-12/3',
    'small_bert/bert_en_uncased_L-2_H-128_A-2':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-2_H-128_A-2/2',
    'small_bert/bert_en_uncased_L-2_H-256_A-4':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-2_H-256_A-4/2',
    'small_bert/bert_en_uncased_L-2_H-512_A-8':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-2_H-512_A-8/2',
    'small_bert/bert_en_uncased_L-2_H-768_A-12':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-2_H-768_A-12/2',
    'small_bert/bert_en_uncased_L-4_H-128_A-2':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-128_A-2/2',
    'small_bert/bert_en_uncased_L-4_H-256_A-4':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-256_A-4/2',
    'small_bert/bert_en_uncased_L-4_H-512_A-8':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2',
    'small_bert/bert_en_uncased_L-4_H-768_A-12':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-768_A-12/2',
    'small_bert/bert_en_uncased_L-6_H-128_A-2':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-6_H-128_A-2/2',
    'small_bert/bert_en_uncased_L-6_H-256_A-4':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-6_H-256_A-4/2',
    'small_bert/bert_en_uncased_L-6_H-512_A-8':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-6_H-512_A-8/2',
    'small_bert/bert_en_uncased_L-6_H-768_A-12':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-6_H-768_A-12/2',
    'small_bert/bert_en_uncased_L-8_H-128_A-2':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-128_A-2/2',
    'small_bert/bert_en_uncased_L-8_H-256_A-4':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-256_A-4/2',
    'small_bert/bert_en_uncased_L-8_H-512_A-8':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2',
    'small_bert/bert_en_uncased_L-8_H-768_A-12':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-768_A-12/2',
    'small_bert/bert_en_uncased_L-10_H-128_A-2':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-10_H-128_A-2/2',
    'small_bert/bert_en_uncased_L-10_H-256_A-4':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-10_H-256_A-4/2',
    'small_bert/bert_en_uncased_L-10_H-512_A-8':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-10_H-512_A-8/2',
    'small_bert/bert_en_uncased_L-10_H-768_A-12':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-10_H-768_A-12/2',
    'small_bert/bert_en_uncased_L-12_H-128_A-2':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-128_A-2/2',
    'small_bert/bert_en_uncased_L-12_H-256_A-4':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-256_A-4/2',
    'small_bert/bert_en_uncased_L-12_H-512_A-8':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-512_A-8/2',
    'small_bert/bert_en_uncased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-768_A-12/2',
    'albert_en_base':
        'https://tfhub.dev/tensorflow/albert_en_base/2',
    'electra_small':
        'https://tfhub.dev/google/electra_small/2',
    'electra_base':
        'https://tfhub.dev/google/electra_base/2',
    'experts_pubmed':
        'https://tfhub.dev/google/experts/bert/pubmed/2',
    'experts_wiki_books':
        'https://tfhub.dev/google/experts/bert/wiki_books/2',
    'talking-heads_base':
        'https://tfhub.dev/tensorflow/talkheads_ggelu_bert_en_base/1',
}
map_model_to_preprocess = {
    'bert_en_uncased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'bert_en_cased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_cased_preprocess/3',
    'bert_en_wwm_cased_L-24_H-1024_A-16':
        'https://tfhub.dev/tensorflow/bert_en_cased_preprocess/3',
    'small_bert/bert_en_uncased_L-2_H-128_A-2':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-2_H-256_A-4':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-2_H-512_A-8':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-2_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-4_H-128_A-2':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-4_H-256_A-4':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-4_H-512_A-8':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-4_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-6_H-128_A-2':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-6_H-256_A-4':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-6_H-512_A-8':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-6_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-8_H-128_A-2':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-8_H-256_A-4':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-8_H-512_A-8':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-8_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-10_H-128_A-2':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-10_H-256_A-4':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-10_H-512_A-8':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-10_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-12_H-128_A-2':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-12_H-256_A-4':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-12_H-512_A-8':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'small_bert/bert_en_uncased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'bert_multi_cased_L-12_H-768_A-12':
        'https://tfhub.dev/tensorflow/bert_multi_cased_preprocess/3',
    'albert_en_base':
        'https://tfhub.dev/tensorflow/albert_en_preprocess/3',
    'electra_small':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'electra_base':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'experts_pubmed':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'experts_wiki_books':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
    'talking-heads_base':
        'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
}


def print_my_examples(inputs, results):
    result_for_printing = \
        [f'input: {inputs[i]:<30} : score: {results[i][0]:.6f}'
         for i in range(len(inputs))]
    print(*result_for_printing, sep='\n')


class BERT:

    def __init__(self, tweets):
        self._tweets = tweets
        self._ids = []
        self._texts = []
        for (t_id, t_text) in tweets:
            self._ids.append(t_id)
            self._texts.append(t_text)

        self._tfhub_handle_preprocess = map_model_to_preprocess['small_bert/bert_en_uncased_L-4_H-512_A-8']
        self._tfhub_handle_encoder = map_name_to_handle['small_bert/bert_en_uncased_L-4_H-512_A-8']
        self._train_ds = None
        self._val_ds = None
        self._test_ds = None

    def input_processing(self):
        print("processing")

        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, 'pan20-author-profiling/texts/train/en')

        print(module_dir)
        print(file_path)

        AUTOTUNE = tf.data.AUTOTUNE
        batch_size = 12
        seed = 42

        raw_train_ds = tf.keras.preprocessing.text_dataset_from_directory(
            file_path,
            batch_size=batch_size,
            validation_split=0.2,
            subset='training',
            seed=seed)

        self._train_ds = raw_train_ds.cache().prefetch(buffer_size=AUTOTUNE)

        self._val_ds = tf.keras.preprocessing.text_dataset_from_directory(
            file_path,
            batch_size=batch_size,
            validation_split=0.2,
            subset='validation',
            seed=seed)

        self._val_ds = self._val_ds.cache().prefetch(buffer_size=AUTOTUNE)

        self._test_ds = tf.keras.preprocessing.text_dataset_from_directory(
            os.path.join(module_dir, 'pan20-author-profiling/texts/test/en'),
            batch_size=batch_size)

        self._test_ds = self._test_ds.cache().prefetch(buffer_size=AUTOTUNE)

        # call next
        # self.preprocessing_model()
        self.define_model()

    def preprocessing_model(self):
        print("pre-processing")
        bert_preprocess_model = hub.KerasLayer(self._tfhub_handle_preprocess)
        text_preprocessed = bert_preprocess_model(self._texts)
        # call next
        self.define_model()

    def build_classifier_model(self):
        print("building classifier")
        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
        preprocessing_layer = hub.KerasLayer(self._tfhub_handle_preprocess, name='preprocessing')
        encoder_inputs = preprocessing_layer(text_input)
        encoder = hub.KerasLayer(self._tfhub_handle_encoder, trainable=True, name='BERT_encoder')
        outputs = encoder(encoder_inputs)
        net = outputs['pooled_output']
        net = tf.keras.layers.Dropout(0.1)(net)
        net = tf.keras.layers.Dense(1, activation=None, name='classifier')(net)
        return tf.keras.Model(text_input, net)

    def define_model(self):
        classifier_model = self.build_classifier_model()
        print("defining model")
        # bert_raw_result = classifier_model(tf.constant(self._texts)
        # print(tf.sigmoid(bert_raw_result))
        # call next
        self.train_model(classifier_model)

    def train_model(self, classifier_model):
        print("training model")
        # loss function
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
        metrics = tf.metrics.BinaryAccuracy()

        # Optimizer
        epochs = 5
        steps_per_epoch = tf.data.experimental.cardinality(self._train_ds).numpy()
        num_train_steps = steps_per_epoch * epochs
        num_warmup_steps = int(0.1 * num_train_steps)

        init_lr = 3e-5
        optimizer = optimization.create_optimizer(init_lr=init_lr,
                                                  num_train_steps=num_train_steps,
                                                  num_warmup_steps=num_warmup_steps,
                                                  optimizer_type='adamw')

        # Loading the BERT model and training
        classifier_model.compile(optimizer=optimizer,
                                 loss=loss,
                                 metrics=metrics)

        history = classifier_model.fit(x=self._train_ds,
                                       validation_data=self._val_ds,
                                       epochs=epochs)

        # Evaluate the model
        loss, accuracy = classifier_model.evaluate(self._test_ds)

        print(f'Loss: {loss}')
        print(f'Accuracy: {accuracy}')

        self.test_model(classifier_model)
        #self.export_model(classifier_model)
        self.reload_model()

    def test_model(self, classifier_model):
        print("testing model")
        examples = [
            'COVID is a fake! There are stealing from us with all those lies',
            'Covid19 is a danger for humanity, we need to take care of ourselves',
            'PLANDEMIC!!! GOVERMENT OUT!!! President TRUMP won the elections, its all false!',
            'The Public Relations Officer For Zone 2 Police Command, #USER#, Gives Advice To Partners On #HASHTAG#.', #NO,
            'With Obama’s Approval, Russia Selling 130 Tons of Uranium to Iran #URL# Under the New Trump Standard, '
            'Why Wasn"t Obama Impeached? ' #SI
        ]
        original_results = tf.sigmoid(classifier_model(tf.constant(examples)))

        print('Results from the model in memory:')
        print_my_examples(examples, original_results)

    def export_model(self, classifier_model):
        dataset_name = 'fake_news_twitter'
        module_dir = os.path.dirname(__file__)  # get current directory
        saved_model_path = os.path.join(module_dir, '{}_bert'.format(dataset_name.replace('/', '_')))

        classifier_model.save(saved_model_path, include_optimizer=False)

    def reload_model(self):
        dataset_name = 'fake_news_twitter'
        module_dir = os.path.dirname(__file__)  # get current directory
        saved_model_path = os.path.join(module_dir, '{}_bert'.format(dataset_name.replace('/', '_')))

        reloaded_model = tf.saved_model.load(saved_model_path)

        examples = [
            'COVID is a fake! There are stealing from us with all those lies',
            'Covid19 is a danger for humanity, we need to take care of ourselves',
            'PLANDEMIC!!! GOVERMENT OUT!!! President TRUMP won the elections, its all false!',
            'The Public Relations Officer For Zone 2 Police Command, #USER#, Gives Advice To Partners On #HASHTAG#.', #NO,
            'With Obama’s Approval, Russia Selling 130 Tons of Uranium to Iran #URL# Under the New Trump Standard, '
            'Why Wasn"t Obama Impeached? ' #SI
        ]
        reloaded_results = tf.sigmoid(reloaded_model(tf.constant(self._texts)))

        print('Results from the saved model:')
        print_my_examples(self._texts, reloaded_results)

        dict_results = {}
        for i in range(len(self._ids)):
            dict_results[self._ids[i]] = reloaded_results[i][0]

        return dict_results
