import { useNavigate } from "react-router-dom";
import CourseCard from "./CourseCard";
import Checkbox from "../common/Checkbox";
import type { CourseItem } from "../../types/mycourse";

interface MyCourseContentProps {
    groupedCourses: [string, CourseItem[]][];
    isEmptyCurrentCourses: boolean;
    isEditMode: boolean;
    selectedCourses: number[];
    onNavigateToCourse: (courseId: number) => void;
    onSelectCourse: (courseId: number) => void;
}

export default function MyCourseContent({
    groupedCourses,
    isEmptyCurrentCourses,
    isEditMode,
    selectedCourses,
    onNavigateToCourse,
    onSelectCourse,
}: MyCourseContentProps) {
    const navigate = useNavigate();

    return (
        <main className="flex-1 px-5">
            {isEmptyCurrentCourses ? (
                <div className="flex flex-col items-center justify-center pt-24 px-6 text-center">
                    <h1 className="text-black font-bold mb-1 text-[16px]">
                        아직 저장한 코스가 없어요
                    </h1>
                    <p className="text-black text-sm font-semi-bold mb-8 leading-relaxed">
                        영상 코스를 둘러보고 여행을 계획해 보세요
                    </p>
                    <button
                        onClick={() => navigate('/')}
                        className="bg-[#42BCEB] text-white px-10 py-3 rounded-xl font-bold shadow-m shadow-blue-100 active:scale-95 transition-transform"
                    >
                        코스 둘러보기
                    </button>
                </div>
            ) : (
                <div className="mt-2 space-y-6">
                    {groupedCourses.map(([month, courses]) => (
                        <div key={month}>
                            <h2 className="text-[16px] font-bold text-gray-900 mb-3 ml-1">
                                {month}
                            </h2>
                            <div className="space-y-4">
                                {courses.map(course => {
                                    const isSelected = selectedCourses.includes(course.courseId);
                                    return (
                                        <div
                                            key={course.courseId}
                                            className="flex items-center gap-3"
                                        >
                                            {isEditMode && (
                                                <div className="flex-shrink-0">
                                                    <Checkbox
                                                        checked={isSelected}
                                                        onChange={() => onSelectCourse(course.courseId)}
                                                    />
                                                </div>
                                            )}
                                            <div
                                                className={`flex-1 rounded-2xl transition-all ${isEditMode && isSelected
                                                    ? "bg-blue-50 border border-[#42BCEB]"
                                                    : "border border-[#E8E8E8]"
                                                    }`}
                                            >
                                                <CourseCard
                                                    {...course}
                                                    onClick={() => {
                                                        if (isEditMode) {
                                                            onSelectCourse(course.courseId);
                                                        } else {
                                                            onNavigateToCourse(course.courseId);
                                                        }
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </main>
    );
}