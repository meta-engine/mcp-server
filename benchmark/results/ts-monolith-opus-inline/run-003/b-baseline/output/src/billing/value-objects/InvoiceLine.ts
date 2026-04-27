import { Money } from "../../shared/value-objects/Money";

/** A line item on an Invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
