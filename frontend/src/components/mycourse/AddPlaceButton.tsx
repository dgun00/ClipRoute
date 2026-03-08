import addIcon from '../../assets/icons/add-icon.svg';

interface AddPlaceButtonProps {
    onClick: () => void;
}

const AddPlaceButton = ({ onClick }: AddPlaceButtonProps) => {
    return (
        <div className="flex justify-center w-full py-2">
            <button
                onClick={onClick}
                className="p-[0.71025rem] rounded-full flex items-center justify-center active:scale-95 transition-all shadow-sm"
                style={{
                    background: "linear-gradient(#fff, #fff) padding-box, linear-gradient(to bottom, #42BCEB, #8EE0F7) border-box",
                    border: "1.8px solid transparent",
                }}
            >
                <img src={addIcon} alt="장소 추가 버튼" className="w-[1.6875rem] h-[1.6875rem]" />
            </button>
        </div>
    );
};


export default AddPlaceButton;
