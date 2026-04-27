import { Money } from "../../shared/value-objects/Money";

/** A single line item on an invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
