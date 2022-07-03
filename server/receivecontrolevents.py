import logging
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from tkinter import messagebox

connection_str = 'Endpoint=sb://sensorhub.servicebus.windows.net/;SharedAccessKeyName=sendreceive;SharedAccessKey=Qbk8hzxLB2TRmnczYnZmNTR/wvHiR5PZAhB8xacxc2U=;EntityPath=controlevents'
consumer_group = '$Default'
eventhub_name = 'controlevents'

logger = logging.getLogger("azure.eventhub")
logging.basicConfig(level=logging.INFO)

async def on_event(partition_context, event):
    logger.info("Received event from partition {}".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)
    print(event.message)#body_as_str()
    #messagebox.showinfo('Ahem..Ahem',event.message)

async def receive():
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group, eventhub_name=eventhub_name)
    async with client:
        await client.receive(
            on_event=on_event,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )
        # receive events from specified partition:
        # await client.receive(on_event=on_event, partition_id='0')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive())