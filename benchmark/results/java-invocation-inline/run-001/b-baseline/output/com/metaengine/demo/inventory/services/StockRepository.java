package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** Persistence gateway for stock items. */
public class StockRepository {
    /** Persist a new stock item from the provided partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a stock item by id. Returns null when not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} stock items. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove a stock item by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
