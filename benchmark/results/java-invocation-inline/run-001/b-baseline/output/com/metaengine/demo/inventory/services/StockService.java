package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** Application service exposing stock item operations. */
public class StockService {
    /** Create a stock item from the provided partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a stock item by id. Returns null when not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} stock items. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a stock item by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
