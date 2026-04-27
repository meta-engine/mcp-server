package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** Reservation service for the StockItem aggregate. */
public class ReservationService {

    /** Reserve a new StockItem from a partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a reserved StockItem by id; returns null if not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List reserved StockItems, capped at the supplied limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Release a reservation by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
