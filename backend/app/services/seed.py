from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.entities import Quiz, User


async def seed_demo_data(session: AsyncSession) -> None:
    user_count = len((await session.scalars(select(User.id))).all())
    if user_count:
        return

    organizer = User(
        id='u-organizer',
        email='organizer@quiz.test',
        name='12345',
        password_hash=hash_password('123456'),
        role='user',
    )
    player = User(
        id='u-player',
        email='player@quiz.test',
        name='Player',
        password_hash=hash_password('123456'),
        role='user',
    )
    sample_quiz = Quiz(
        id='q-geography',
        owner_id=organizer.id,
        title='Квиз по географии',
        category='География',
        time_limit=45,
        rules='За каждый верный ответ начисляется 100 очков. Для вопросов с несколькими ответами нужно выбрать все правильные варианты.',
        questions=[
            {
                'id': 'question-1',
                'title': 'Собор на фотографии',
                'type': 'image',
                'image': '/assets/sagrada.png',
                'imageCaption': 'Какие еще знаменитые соборы вы знаете, которые находятся в той же части света, что и данный?',
                'multi': True,
                'timeLimit': 450,
                'answers': [
                    {'id': 'a1', 'text': 'Миланский', 'correct': True},
                    {'id': 'a2', 'text': 'Богоматери Ангелов', 'correct': False},
                    {'id': 'a3', 'text': 'Кёльнский', 'correct': True},
                    {'id': 'a4', 'text': 'Святого Петра', 'correct': True},
                ],
            },
            {
                'id': str(uuid4()),
                'title': 'Экспедиция',
                'type': 'text',
                'multi': False,
                'timeLimit': 500,
                'body': 'Эта экспедиция, организованная в XVIII веке, имеет несколько названий. Кто был главным командиром экспедиции?',
                'answers': [
                    {'id': 'b1', 'text': 'С. Дежнёв', 'correct': False},
                    {'id': 'b2', 'text': 'В. Беринг', 'correct': True},
                    {'id': 'b3', 'text': 'И. Крузенштерн', 'correct': False},
                    {'id': 'b4', 'text': 'Ф. Врангель', 'correct': False},
                ],
            },
        ],
    )
    session.add_all([organizer, player, sample_quiz])
    await session.commit()
