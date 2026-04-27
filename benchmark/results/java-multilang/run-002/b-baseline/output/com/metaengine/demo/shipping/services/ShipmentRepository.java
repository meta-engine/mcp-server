package com.metaengine.demo.shipping.services;

import java.util.List;
import com.metaengine.demo.shipping.aggregates.Shipment;

/** ShipmentRepository in the shipping domain. */
public class ShipmentRepository {
    /** Create a new Shipment. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Shipment by id. Returns null if not found. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Shipments up to limit. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
