import { useState } from "react";
import { deleteMyCourses } from "../api/myCourse"; // 새로 만들어야 함

export function useDeleteCourses() {
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleDelete = async (courseIds: number[]) => {
        setIsDeleting(true);
        setError(null);
        try {
            await deleteMyCourses(courseIds);
            return true;
        } catch (err) {
            setError(err instanceof Error ? err.message : "삭제 실패");
            return false;
        } finally {
            setIsDeleting(false);
        }
    };

    return { handleDelete, isDeleting, error };
}