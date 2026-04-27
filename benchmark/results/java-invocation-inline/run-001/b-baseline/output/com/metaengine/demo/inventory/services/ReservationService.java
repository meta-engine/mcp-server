package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** Domain service that reserves stock for downstream consumers. */
public class ReservationService {
    /** Reserve stock from the provided partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a reserved stock item by id. Returns null when not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} reserved stock items. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Release a reservation for the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
