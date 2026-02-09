import { createBrowserRouter, RouterProvider } from "react-router-dom";
import './index.css'
import MobileLayout from "./layouts/MobileLayout";
import LoginPage from "./Pages/LoginPage"; 
import HomePage from "./Pages/HomePage"; 
import SignupPage from "./Pages/SignupPage";
import CoursePage from "./Pages/CoursePage";
import LoadingPage from "./Pages/LoadingPage";
import MyPage from "./Pages/MyPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MobileLayout />, // 공통 레이아웃을 부모로 설정
    children: [
      {
        path: "/",
        element: <HomePage/>
      },
      {
        path: "/home",
        element: <HomePage /> 
      },
      {
        path: "/login",
        element: <LoginPage />
      },
      {
        path: "/signup",
        element: <SignupPage /> 
      },
      {
        path: "/my",
        element: <MyPage /> 
      },
      { path: "/course/:videoId", element: <CoursePage /> },
      { path: "/loading", element: <LoadingPage /> },
    ]
  }
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;