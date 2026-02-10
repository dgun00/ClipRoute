package com.example.cliproute.domain.place.repository;

import com.example.cliproute_project.domain.place.entity.Place;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;

public interface PlaceRepository extends JpaRepository<Place, Long>, PlaceRepositoryCustom {
    // [10 API]
    List<Place> findAllByIdInAndDeletedAtIsNull(Collection<Long> ids);
}
