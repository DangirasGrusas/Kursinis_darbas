import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import Port_manager_helper

class TestCargoPortManager(unittest.TestCase):

    @patch('Port_manager_helper.pd.read_csv')
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_submit_ship_empty_csv(self, mock_read_csv):
        Port_manager_helper.ship_entry.get.return_value = '1'  
        Port_manager_helper.imo_entry.get.return_value = '1234567'  
        mock_read_csv.side_effect = lambda x: pd.DataFrame(columns=['ID', 'Full Name', 'Field', 'Activity', 'IMO Number'], index=[';'])
        self.assertFalse(Port_manager_helper.submit())

    @patch.object(Port_manager_helper, 'is_imo_in_port', MagicMock(return_value=True))
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_submit_ship_existing_imo(self):
        Port_manager_helper.ship_entry.get.return_value = '1'  
        Port_manager_helper.imo_entry.get.return_value = '1234567' 
        self.assertFalse(Port_manager_helper.submit())

    @patch.object(Port_manager_helper, 'is_imo_in_port', MagicMock(return_value=False))
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_leave_ship_nonexistent_imo(self):
        Port_manager_helper.ship_entry.get.return_value = '2'
        Port_manager_helper.imo_entry.get.return_value = '1234567'
        self.assertFalse(Port_manager_helper.submit())

    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_submit_ship_invalid_selection(self):
        Port_manager_helper.ship_entry.get.return_value = '3'
        Port_manager_helper.imo_entry.get.return_value = '1234567' 
        self.assertFalse(Port_manager_helper.submit())

    @patch('Port_manager_helper.update_workers_activity_to_free')
    @patch('Port_manager_helper.pd.read_csv')
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_leave_ship_update_workers(self, mock_read_csv, mock_update_workers):
        Port_manager_helper.ship_entry.get.return_value = '2'
        Port_manager_helper.imo_entry.get.return_value = '1234567'
        mock_read_csv.return_value = pd.DataFrame({'IMO Number': ['1234567']}, index=[';'])
        self.assertTrue(Port_manager_helper.submit())
        mock_update_workers.assert_called_once_with('1234567')


    @patch('Port_manager_helper.pd.read_csv')
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_leave_ship_success(self, mock_read_csv):
        Port_manager_helper.ship_entry.get.return_value = '2' 
        Port_manager_helper.imo_entry.get.return_value = '1234567'
        mock_read_csv.return_value = pd.DataFrame(columns=['IMO Number'], index=[';'])
        self.assertTrue(Port_manager_helper.submit())

    @patch('Port_manager_helper.pd.read_csv')
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_submit_ship_port_full(self, mock_read_csv):
        Port_manager_helper.ship_entry.get.return_value = '1' 
        Port_manager_helper.imo_entry.get.return_value = '1234567'
        mock_read_csv.return_value = pd.DataFrame(columns=['ID', 'Full Name', 'Field', 'Activity', 'IMO Number'], index=[';'])
        port_space = 0  
        with patch.object(Port_manager_helper, 'port', MagicMock(space=port_space)):
            self.assertFalse(Port_manager_helper.submit())

    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_leave_ship_not_docked(self):
        Port_manager_helper.ship_entry.get.return_value = '2'  
        Port_manager_helper.imo_entry.get.return_value = '1234567' 
        with patch.object(Port_manager_helper, 'is_imo_in_port', MagicMock(return_value=False)):
            self.assertFalse(Port_manager_helper.submit())

    @patch('Port_manager_helper.pd.read_csv')
    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_submit_ship_not_enough_workers(self, mock_read_csv):
        Port_manager_helper.ship_entry.get.return_value = '1'
        Port_manager_helper.imo_entry.get.return_value = '1234567'
        mock_read_csv.return_value = pd.DataFrame(columns=['ID', 'Full Name', 'Field', 'Activity', 'IMO Number'], index=[';'])
        workers = [MagicMock(activity='Busy') for _ in range(6)]
        with patch('Port_manager_helper.create_workers_from_csv', MagicMock(return_value=workers)):
            self.assertFalse(Port_manager_helper.submit())

    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    @patch('Port_manager_helper.pd.read_csv')
    def test_leave_ship_success_update_workers(self, mock_read_csv):
        Port_manager_helper.ship_entry.get.return_value = '2' 
        Port_manager_helper.imo_entry.get.return_value = '1234567'
        mock_read_csv.return_value = pd.DataFrame({'IMO Number': ['1234567']}, index=[';'])
        with patch('Port_manager_helper.update_workers_activity_to_free', MagicMock()) as mock_update_workers:
            self.assertTrue(Port_manager_helper.submit())
            mock_update_workers.assert_called_once_with('1234567')

    @patch.object(Port_manager_helper, 'ship_entry', MagicMock())
    @patch.object(Port_manager_helper, 'imo_entry', MagicMock())
    def test_leave_ship_invalid_imo(self):
        Port_manager_helper.ship_entry.get.return_value = '2' 
        Port_manager_helper.imo_entry.get.return_value = 'abc' 
        self.assertFalse(Port_manager_helper.submit())

if __name__ == '__main__':
    unittest.main()
