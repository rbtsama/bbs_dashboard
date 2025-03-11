import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import Dashboard from './pages/Dashboard';
import Rankings from './pages/Rankings';
import FollowsPage from './pages/Follows';
import CarListPage from './pages/CarList';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: '/',
        element: <Dashboard />,
      },
      {
        path: '/dashboard',
        element: <Dashboard />,
      },
      {
        path: '/rankings',
        element: <Rankings />,
      },
      {
        path: '/follows',
        element: <FollowsPage />,
      },
      {
        path: '/cars',
        element: <CarListPage />,
      },
    ],
  },
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
}); 