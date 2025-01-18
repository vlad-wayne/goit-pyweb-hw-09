import pika
import random
from faker import Faker
from models import Contact


RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'email_queue'

def main():
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    
    channel.queue_declare(queue=QUEUE_NAME)

    
    fake = Faker()
    for _ in range(10):  
        fullname = fake.name()
        email = fake.email()

        
        contact = Contact(fullname=fullname, email=email)
        contact.save()

        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=str(contact.id)
        )
        print(f"Відправлено контакт {contact.fullname} з ID {contact.id}")

    
    connection.close()

if __name__ == "__main__":
    main()
