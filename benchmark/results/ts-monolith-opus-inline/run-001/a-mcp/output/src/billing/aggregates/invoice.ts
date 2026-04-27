import { Id } from '../../shared/value-objects/id';
import { InvoiceStatus } from '../enums/invoice-status.enum';
import { Money } from '../../shared/value-objects/money';

/** Invoice aggregate root for the billing module. */
export class Invoice {

  constructor(public id: Id, public orderId: Id, public status: InvoiceStatus, public totalAmount: Money) { }
}
