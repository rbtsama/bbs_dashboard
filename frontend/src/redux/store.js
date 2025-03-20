import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import followReducer from './reducers/followReducer';

const rootReducer = combineReducers({
  follow: followReducer,
});

const store = createStore(rootReducer, applyMiddleware(thunk));

export default store; 