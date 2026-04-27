import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';
import { InvoiceStatus } from '../enums/InvoiceStatus';

/** Invoice aggregate */
export class Invoice {
  constructor(
    public readonly id: Id,
    public readonly orderId: Id,
    public readonly status: InvoiceStatus,
    public readonly totalAmount: Money,
  ) {}
}
