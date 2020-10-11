from rest_framework import serializers  
from userauth.models import UserModel
from .models import ChatModel


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatModel
        fields = ['sender', 'reciever', 'message', 'send_date', 'seen']


    def to_representation(self, instance):
        rep = super(ChatSerializer, self).to_representation(instance)
        rep['sender'] = instance.sender.username
        rep['reciever'] = instance.reciever.username
        rep['seen'] = 'seen' if instance.seen else 'not seen' 
        return rep
