export const MOCK_COURSE_DETAIL = {
  isSuccess: true,
  code: "SUCCESS",
  message: "성공",
  result: {
    courseId: 1,
    videoTitle: "부산 2박 3일 여행 코스",
    videoUrl: "https://youtube.com/watch?v=example",
    thumbnailUrl: "https://example.com/thumbnail.jpg",
    channelName: "여행유튜버",
    regionId: 1,
    regionName: "부산",
    isScrapped: false,
    travelStatus: "BEFORE" as const,
    itineraries: [
      {
        visitDay: 1,
        places: [
          {
            coursePlaceId: 1,
            visitOrder: 1,
            placeId: 101,
            placeName: "벡스코",
            placeCategory: "전시관",
            address: "부산 해운대구 APEC로 55",
            lat: 35.1689,
            lng: 129.1360,
            timestamp: 0
          },
          {
            coursePlaceId: 2,
            visitOrder: 2,
            placeId: 102,
            placeName: "해운대 해수욕장",
            placeCategory: "관광명소",
            address: "부산 해운대구 우동",
            lat: 35.1587,
            lng: 129.1604,
            timestamp: 300
          }
        ]
      },
      {
        visitDay: 2,
        places: [
          {
            coursePlaceId: 3,
            visitOrder: 1,
            placeId: 103,
            placeName: "장산",
            placeCategory: "산",
            address: "부산 해운대구 좌동",
            lat: 35.1972,
            lng: 129.1481,
            timestamp: 0
          }
        ]
      }
    ]
  }
};