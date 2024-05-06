import unittest, sys, os
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from src.database.models import User
from src.database.schemas import UserDBSchema
from src.repository.users import get_user_by_email, create_user, user_email_confirmation, update_user_avatar, update_user_token

class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_valid = User(
            id=1,
            username='John',
            email='john@mail.com',
            pwd_hash='jhgadfueagdfjaegfja',
            avatar='http://cloudinary/image.jpg',
            refresh_token='skshfhefwhefwehfwehfwehf',
            confirmed=False)

        cls.user_invalid = {
            'username': 'Doe',
            'email': 'doe@fake.com',
            'password': 'password'}

        cls.user_db_creation = {
            'username': 'Doe',
            'email': 'doe@fake.com',
            'pwd_hash': 'password'}

    def setUp(self):
        self.moked_db_responce = MagicMock()
        # self.session = MagicMock(spec=Session)
        self.local_session = AsyncMock(spec=AsyncSession)
        self.local_session.execute.return_value = self.moked_db_responce

        
    # @unittest.skip('not implemented')
    async def test_get_user_by_email_valid(self):
        email = self.user_valid.email
        self.moked_db_responce.scalar_one_or_none.return_value = self.user_valid

        result = await get_user_by_email(email=email , db=self.local_session)
        
        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(self.moked_db_responce.scalar_one_or_none.call_count, 1)

        self.assertEqual(result, self.user_valid)

    # @unittest.skip('not implemented')
    async def test_get_user_by_email_invalid(self):
        email = self.user_invalid['email']
        self.moked_db_responce.scalar_one_or_none.return_value = None

        result = await get_user_by_email(email=email, db=self.local_session)

        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalar_one_or_none.call_count, 1)

        self.assertIsNone(result)

    # @unittest.skip('not implemented')
    async def test_create_user(self):
        body = UserDBSchema(**self.user_db_creation)
        self.moked_db_responce.scalar_one_or_none.return_value = User(
            **self.user_db_creation)

        result = await create_user(body=body, db=self.local_session)
        
        self.assertEqual(self.local_session.add.call_count, 1)
        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(self.local_session.refresh.call_count, 1)
        self.assertIsInstance(result, User)

        # self.assertDictContainsSubset(self.user_db_creation, result.__dict__)
        self.assertLessEqual(self.user_db_creation.items(), result.__dict__.items())

    # @unittest.skip('not implemented')
    async def test_update_user_token(self):
        user = self.user_valid
        token = 'eruweutweyitewyewt'

        result = await update_user_token(user=user, token=token, db=self.local_session)
        
        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(self.local_session.refresh.call_count, 1)
        self.assertIsInstance(result, User)

        self.assertEqual(result.refresh_token, token)

    # @unittest.skip('not implemented')
    async def test_user_email_confirmation(self):
        user=self.user_valid

        result = await user_email_confirmation(user=user, db=self.local_session)

        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(self.local_session.refresh.call_count, 1)
        self.assertIsInstance(result, User)

        self.assertTrue(result.confirmed)

    # @unittest.skip('not implemented')
    async def test_update_user_avatar(self):
        user = self.user_valid
        url = 'http://avatar.domain.com/avatar.jpg'

        result = await update_user_avatar(user=user, url=url, db=self.local_session)

        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(self.local_session.refresh.call_count, 1)
        self.assertIsInstance(result, User)

        self.assertEqual(result.avatar, url)

if __name__ == '__main__':
    
    unittest.main()