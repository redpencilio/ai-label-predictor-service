import torch
import torch.nn as nn
from transformers import AutoModel


class BertClassifier(nn.Module):

    def __init__(self, config):
        super(BertClassifier, self).__init__()
        # Binary classification problem (num_labels = 2)
        self.num_labels = config["num_labels"]
        # Pre-trained BERT model
        self.bert = AutoModel.from_pretrained("GroNLP/bert-base-dutch-cased")
        # Dropout to avoid overfitting
        self.dropout = nn.Dropout(config['hidden_dropout_prob'])
        # A single layer classifier added on top of BERT to fine tune for binary classification
        self.classifier = nn.Sequential(
            nn.Linear(config['hidden_size'], config['hidden_size']),
            nn.Sigmoid(),
            nn.Linear(config['hidden_size'], config['num_labels']),
            nn.Softmax(dim=1),

        )

        self.id_dict = {}

    def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                position_ids=None, head_mask=None):
        # Forward pass through pre-trained BERT
        outputs = self.bert(input_ids, position_ids=position_ids, token_type_ids=token_type_ids,
                            attention_mask=attention_mask, head_mask=head_mask)

        pooled_output = outputs[-1]

        pooled_output = self.dropout(pooled_output)
        return self.classifier(pooled_output)
