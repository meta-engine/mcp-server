package com.metaengine.demo.inventory.services;

import java.util.List;

import com.metaengine.demo.inventory.aggregates.StockItem;

/** ReservationService for the inventory domain. */
public class ReservationService {

    /** Creates a new StockItem from the partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds a StockItem by id. May return null. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists StockItems up to the given limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the StockItem with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
