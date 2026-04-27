import { Money } from "../../shared/value-objects/Money";

/** Single billable line within an invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
