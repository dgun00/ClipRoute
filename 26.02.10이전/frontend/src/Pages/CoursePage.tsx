import GoogleMap from '../components/GoolgeMap';
import MapHeader from '../components/MapHeader';
import PlaceBottomSheet from '../components/course/PlaceBottomSheet';
import positionicon from "../../src/assets/icons/positon-icon.svg";

const MOCK_PLACES = [
  { id: 1, day: 1, order: 1, name: "벡스코", category: "전시관", address: "부산 해운대구 APEC로 55", lat: 35.1689, lng: 129.1360 },
  { id: 2, day: 1, order: 2, name: "해운대 해수욕장", category: "관광명소", address: "부산 해운대구 우동", lat: 35.1587, lng: 129.1604 },
  { id: 3, day: 2, order: 3, name: "장산", category: "산", address: "부산 해운대구 좌동", lat: 35.1972, lng: 129.1481 },
];

const CoursePage = () => {
  return (
    <div className="relative w-screen h-screen overflow-hidden">
      <GoogleMap places={MOCK_PLACES} />
      <MapHeader/>
      <PlaceBottomSheet places={MOCK_PLACES} />
      <button className="absolute bottom-[100px] right-4 z-10 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center">
        <img src={positionicon}/>
      </button>
    </div>
  );
};

export default CoursePage;