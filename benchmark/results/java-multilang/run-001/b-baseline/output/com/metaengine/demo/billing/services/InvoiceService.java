package com.metaengine.demo.billing.services;

import java.util.List;

import com.metaengine.demo.billing.aggregates.Invoice;

/** InvoiceService for the billing domain. */
public class InvoiceService {

    /** Creates a new Invoice from the partial input. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds an Invoice by id. May return null. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Invoices up to the given limit. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the Invoice with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
