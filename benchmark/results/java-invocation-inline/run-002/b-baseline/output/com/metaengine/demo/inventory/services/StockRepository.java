package com.metaengine.demo.inventory.services;

import java.util.List;

import com.metaengine.demo.inventory.aggregates.StockItem;

/** StockRepository for the inventory domain. */
public class StockRepository {

    /** Persist a new StockItem from partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a StockItem by id. Returns null if not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List StockItems up to the given limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the StockItem with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
