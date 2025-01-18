import pika
from models import Contact


RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'email_queue'

def send_email_stub(email):
    """Функція-заглушка для надсилання email."""
    print(f"Імітація надсилання email на {email}")

def callback(ch, method, properties, body):
    """Обробка повідомлення з RabbitMQ."""
    contact_id = body.decode()
    print(f"Отримано контакт ID: {contact_id}")

    
    contact = Contact.objects(id=contact_id).first()
    if contact:
        send_email_stub(contact.email)

        
        contact.is_sent = True
        contact.save()
        print(f"Контакт {contact.fullname} оновлено. Статус: is_sent=True")

    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    
    channel.queue_declare(queue=QUEUE_NAME)

    
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("Очікування повідомлень. Натисніть Ctrl+C для виходу.")
    channel.start_consuming()

if __name__ == "__main__":
    main()