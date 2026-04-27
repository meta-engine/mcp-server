import { Money } from "../../shared/value-objects/Money";

/** A single billable line on an invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
