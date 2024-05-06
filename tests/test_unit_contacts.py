import unittest, sys, os
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from src.database.models import Record, User
from src.database.schemas import RecordSchema, RecordUpdateSchema
from src.repository.contacts import get_contact, get_contacts, get_contacts_query, create_contact, update_contact, delete_contact

class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User(id=1)
        cls.new_contact = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@mail.com',
            'birthday': '1980-11-10',
            'notes': 'John note'
        }
        cls.created_date = datetime.now()
        cls.fake_db_contacts = [
            Record(
                id=1,
                first_name='Austin',
                last_name='Buttler',
                email='austin@example.com',
                birthday='1990-04-08',
                notes='Feyd',
                user_id=cls.user.id,
                updated_at=cls.created_date
            ),
            Record(
                id=2,
                first_name='Timothee',
                last_name='Chalamet',
                email='chalamet@example.com',
                birthday='1996-05-10',
                notes='Paul',
                user_id=cls.user.id,
                updated_at=cls.created_date
            ),
            Record(
                id=3,
                first_name='Rebecca',
                last_name='Ferguson',
                email='ferguson@example.com',
                birthday='1980-10-11',
                notes='Jessica',
                user_id=cls.user.id,
                updated_at=cls.created_date
            )
        ]

    def setUp(self):
        self.moked_db_responce = MagicMock()
        # self.session = MagicMock(spec=Session)
        self.local_session = AsyncMock(spec=AsyncSession)
        self.local_session.execute.return_value = self.moked_db_responce

        
    # @unittest.skip('not implemented')
    async def test_create_contact(self):
        new_user = RecordSchema(**self.new_contact)
        result = await create_contact(user=self.user, body=new_user, db=self.local_session)
        
        self.assertEqual(self.local_session.add.call_count, 1)
        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(self.local_session.refresh.call_count, 1)
        self.assertIsInstance(result, Record)
        self.assertEqual(result.user_id, self.user.id)

    # @unittest.skip('not implemented')
    async def test_get_contact_exist(self):
        record_id = 1
        self.moked_db_responce.scalar_one_or_none.return_value = self.fake_db_contacts[record_id-1]

        result = await get_contact(user=self.user, record_id=record_id, db=self.local_session)
        
        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalar_one_or_none.call_count, 1)

        self.assertEqual(result, self.fake_db_contacts[record_id-1])

    # @unittest.skip('not implemented')
    async def test_get_contact_not_exist(self):
        record_id = 10
        self.moked_db_responce.scalar_one_or_none.return_value = None

        result = await get_contact(user=self.user, record_id=record_id, db=self.local_session)
        
        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalar_one_or_none.call_count, 1)
        self.assertIsNone(result)

    # @unittest.skip('not implemented')
    async def test_update_contact(self):
        record_id = 1
        self.moked_db_responce.scalar_one_or_none.return_value = self.fake_db_contacts[record_id-1]
        record_update = RecordUpdateSchema(**self.new_contact)

        result = await update_contact(user=self.user, record_id=record_id, body=record_update, db=self.local_session)

        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalar_one_or_none.call_count, 1)
        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(self.local_session.refresh.call_count, 1)

        self.assertIsInstance(result, Record)
        self.assertEqual(result.id, record_id)
        self.assertEqual(result.first_name, record_update.first_name)
        self.assertEqual(result.last_name, record_update.last_name)
        self.assertEqual(result.email, record_update.email)
        self.assertEqual(result.birthday, record_update.birthday)
        self.assertEqual(result.notes, record_update.notes)
        self.assertNotEqual(result.updated_at, self.created_date, msg='updated_at should change')

    # @unittest.skip('not implemented')
    async def test_get_contacts(self):
        # self.moked_db_responce.scalars.return_value.all.return_value = self.fake_db_contacts
        self.moked_db_responce.scalars().all.return_value = self.fake_db_contacts

        result = await get_contacts(user=self.user, limit=0, offset=0, db=self.local_session)

        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalars().all.call_count, 1)
        self.assertEqual(result, self.fake_db_contacts)

    # @unittest.skip('not implemented')
    async def test_get_contacts_query(self):
        record_id = 1
        self.moked_db_responce.scalar_one_or_none.return_value = self.fake_db_contacts[record_id-1]
        record = self.fake_db_contacts[record_id-1]
        self.moked_db_responce.scalars().all.return_value = [record]

        result = await get_contacts_query(user=self.user, 
                                        first_name=record.first_name, 
                                        last_name=record.last_name,
                                        email=record.email,
                                        days_to_birthday=1,
                                        limit=0, offset=0, db=self.local_session)

        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalars().all.call_count, 1)
        self.assertEqual(result, [self.fake_db_contacts[record_id-1]])

    # @unittest.skip('not implemented')
    async def test_delete_contact_exist(self):
        record_id = 1
        self.moked_db_responce.scalar_one_or_none.return_value = self.fake_db_contacts[
            record_id-1]
        
        result = await delete_contact(user=self.user, record_id=record_id, db=self.local_session)
        
        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(
            self.moked_db_responce.scalar_one_or_none.call_count, 1)
        self.assertEqual(self.local_session.delete.call_count, 1)
        self.assertEqual(self.local_session.commit.call_count, 1)
        self.assertEqual(result, self.fake_db_contacts[
            record_id-1])
    
    # @unittest.skip('not implemented')
    async def test_delete_contact_not_exist(self):
        record_id = 10
        self.moked_db_responce.scalar_one_or_none.return_value = None

        result = await delete_contact(user=self.user, record_id=record_id, db=self.local_session)

        self.assertEqual(self.local_session.execute.call_count, 1)
        self.assertEqual(self.moked_db_responce.scalar_one_or_none.call_count, 1)
        self.assertEqual(self.local_session.delete.call_count, 0)
        self.assertEqual(self.local_session.commit.call_count, 0)
        self.assertIsNone(result)

if __name__ == '__main__':
    
    unittest.main()