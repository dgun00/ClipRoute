import { useMutation, useQueryClient } from '@tanstack/react-query';
import { scrapCourse } from '../api/courses';

export const useScrapCourse = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ courseId, startDate, endDate }: { courseId: number; startDate?: string | null; endDate?: string | null }) =>
            scrapCourse(courseId, { startDate, endDate }),
        onSuccess: () => {
            // 스크랩 후 내 코스 페이지 서버에서 최신 데이터 받아옴
            queryClient.invalidateQueries({ queryKey: ['myCourses'] });
        },
        onError: (error) => {
            console.error('스크랩 실패:', error);
        }
    });
};
