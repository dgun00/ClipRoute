type TabType = "current" | "completed";

interface MyCoursTabsProps {
    activeTab: TabType;
    setActiveTab: (tab: TabType) => void;
}

export default function MyCourseTabs({ activeTab, setActiveTab }: MyCoursTabsProps) {
    return (
        <div className="px-5">
            <div className="border-b-2 border-gray-200">
                <div className="flex gap-5">
                    <button
                        onClick={() => setActiveTab("current")}
                        className={`py-4 text-sm font-bold relative transition-colors ${activeTab === "current" ? "text-[#34B1E9]" : "text-black"
                            }`}
                    >
                        여행 전
                        {activeTab === "current" && (
                            <div className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-[#34B1E9]"></div>
                        )}
                    </button>

                    <button
                        onClick={() => setActiveTab("completed")}
                        className={`py-4 text-sm font-bold relative transition-colors ${activeTab === "completed" ? "text-[#34B1E9]" : "text-black"
                            }`}
                    >
                        여행 후
                        {activeTab === "completed" && (
                            <div className="absolute bottom-[-1px] left-0 right-0 h-[2px] bg-[#34B1E9]"></div>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}