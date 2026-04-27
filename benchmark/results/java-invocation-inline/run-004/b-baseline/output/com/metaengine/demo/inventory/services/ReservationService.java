package com.metaengine.demo.inventory.services;

import java.util.List;
import com.metaengine.demo.inventory.aggregates.StockItem;

/** ReservationService domain service. */
public class ReservationService {
    /** Create a Reservation against a StockItem. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a StockItem by id; returns null if not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to limit StockItems. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Cancel a reservation by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
