import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/Homepage/index';
import ErrorPage from './pages/ErrorPage';
import ItemUpload from './pages/ItemUpload/index';
import ItemDetail from './pages/ItemDetailsPage';
import ListingOptionPage from './pages/ListingOptionPage';

function App() {
	return (
		<Router>
			<Routes>
				<Route path='/' element={<HomePage />} />
				<Route path='/ListingOptionPage' element={<ListingOptionPage />} />
				<Route path='/ItemUpload' element={<ItemUpload />} />
				<Route path="/items/:itemId" element={<ItemDetail />} />
				<Route path='*' element={<ErrorPage />} />
			</Routes>
		</Router>
	)
}

export default App;