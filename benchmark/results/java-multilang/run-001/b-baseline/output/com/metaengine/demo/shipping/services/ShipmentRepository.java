package com.metaengine.demo.shipping.services;

import java.util.List;

import com.metaengine.demo.shipping.aggregates.Shipment;

/** ShipmentRepository for the shipping domain. */
public class ShipmentRepository {

    /** Persists a new Shipment from the partial input. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds a Shipment by id. May return null. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Shipments up to the given limit. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the Shipment with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
