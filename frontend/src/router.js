import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import Dashboard from './pages/Dashboard';
import Rankings from './pages/Rankings';
import FollowsPage from './pages/Follows';
import CarListPage from './pages/CarList';
import NotFound from './pages/NotFound';
import ErrorBoundary from './components/ErrorBoundary';
import Welcome from './pages/Welcome';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        path: '/',
        element: <Welcome />,
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
      {
        path: '*',
        element: <NotFound />,
      }
    ],
  },
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
}); 