import { useState } from 'react';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import './index.css';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';



import MobileLayout from "./layouts/MobileLayout";
import LoginPage from "./Pages/LoginPage";
import HomePage from "./Pages/HomePage";
import SignupPage from "./Pages/SignupPage";
import CourseDetailPage from "./Pages/CourseDetailPage";
import LoadingPage from "./Pages/LoadingPage";
import MyPage from "./Pages/MyPage";
import ProfilePage from "./Pages/ProfilePage";
import MyCourseDetailPage from './Pages/MyCourseDetailPage';
import MyCoursePage from "./Pages/MycoursePage";
import CourseListPage from "./Pages/CourseListPage";
import SplashScreen from "./Pages/SplashScreen";



const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    element: <MobileLayout />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/home", element: <HomePage /> },
      { path: "/login", element: <LoginPage /> },
      { path: "/signup", element: <SignupPage /> },
      { path: "/my", element: <MyPage /> },
      { path: "/my/profile", element: <ProfilePage /> },
      { path: "/courses/:courseId", element: <CourseDetailPage /> },
      { path: "/loading", element: <LoadingPage /> },
      { path: "/mycourse", element: <MyCoursePage /> },
      { path: "/mycourse/:courseId", element: <MyCourseDetailPage /> },
      { path: "/courses", element: <CourseListPage /> },
    ],
  },
]);


function App() {
  const [showSplash, setShowSplash] = useState(true);

  // 스플래시 종료 핸들러
  const handleSplashFinish = () => {
    setShowSplash(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      {showSplash ? (
        <SplashScreen onFinish={handleSplashFinish} />
      ) : (
        <RouterProvider router={router} />
      )}
      {/* {import.meta.env.DEV && (
        <ReactQueryDevtools initialIsOpen={false} />
      )} */}
    </QueryClientProvider>
  );
}

export default App;