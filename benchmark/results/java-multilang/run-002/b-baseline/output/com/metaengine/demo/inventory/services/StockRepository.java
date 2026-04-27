package com.metaengine.demo.inventory.services;

import java.util.List;
import com.metaengine.demo.inventory.aggregates.StockItem;

/** StockRepository in the inventory domain. */
public class StockRepository {
    /** Create a new StockItem. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a StockItem by id. Returns null if not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List StockItems up to limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a StockItem by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
