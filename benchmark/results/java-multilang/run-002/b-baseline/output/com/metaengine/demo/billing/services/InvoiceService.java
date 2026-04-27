package com.metaengine.demo.billing.services;

import java.util.List;
import com.metaengine.demo.billing.aggregates.Invoice;

/** InvoiceService in the billing domain. */
public class InvoiceService {
    /** Create a new Invoice. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Invoice by id. Returns null if not found. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Invoices up to limit. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Invoice by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
