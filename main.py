from extensions import *
from settings import *

TIME_DURATION_UNITS = (
    ('week', 60 * 60 * 24 * 7),
    ('day', 60 * 60 * 24),
    ('hour', 60 * 60),
    ('min', 60),
    ('sec', 1)
)


def human_time_duration(seconds):
    if seconds == 0:
        return 'now'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)


def get_image():
    image = random.choice(images)
    if not REPEAT:
        images.remove(image)
    return image


def format_image(image):
    return os.path.join(os.getcwd(), 'img', image)


async def handle_chats():
    if not images:
        logging.info('All images have been sent')
        exit(0)
    image = get_image()
    logging.info('Got random image: %s', image)
    image = format_image(image)
    for chat in chats:
        try:
            logging.info('Sending an image to %s...', chat.username if isinstance(chat, User) else chat.title)
            await client.send_file(chat, image)
        except Exception as s:
            logging.error(s)


async def run_pending():
    while True:
        await handle_chats()
        delay = random.randint(*delay_interval)
        logging.info('Waiting %s...', human_time_duration(delay))
        await asyncio.sleep(delay)


if __name__ == '__main__':

    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    if 'DEBUG' in locals() and DEBUG:
        level = logging.DEBUG
    else:
        level = logging.INFO

    if 'TIMESTAMPS' in locals() and TIMESTAMPS:
        format = '[%(levelname)s] (%(asctime)s) | %(message)s'
    else:
        format = '[%(levelname)s] | %(message)s'
    logging.basicConfig(level=level,
                        format=format,
                        datefmt='%d/%m/%Y %I:%M:%S %p')

    images = list(filter(lambda file: not os.path.isfile(file), os.listdir(os.path.join(os.getcwd(), 'img'))))
    logging.debug('Got files: %s', images)

    try:
        client = TelegramClient('anon', API_ID, API_HASH)
        client.start()
    except Exception as e:
        logging.error(e)
        exit(0)

    dialogs = client.get_dialogs()
    try:
        chats = list(map(lambda chat: client.get_entity(chat), CHATS))
        if not chats:
            logging.error('The list of chats is empty, please enter in the variable CHATS in settings.py the list '
                          'of chats you want to send images to')
            exit(0)
    except Exception as e:
        logging.error(e)
        exit(0)

    if 'DELAY' not in locals():
        logging.error('DELAY variable not initialized, please set DELAY variable in settings.py')
        exit(0)

    if isinstance(DELAY, (list, tuple)):
        delay_interval = DELAY
    elif isinstance(DELAY, int):
        delay_interval = (DELAY, DELAY)
    else:
        logging.error('DELAY variable must be integer or random number interval as list or tuple, not %s',
                      type(DELAY).__name__)
        exit(0)

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    try:
        logging.info('Bot starts working')
        asyncio.ensure_future(run_pending())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.info('Bot shutdown')
        loop.close()
