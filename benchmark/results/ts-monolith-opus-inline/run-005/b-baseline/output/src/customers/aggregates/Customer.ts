import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';
import { CustomerStatus } from '../enums/CustomerStatus';
import { Email } from '../value-objects/Email';

/** Customer aggregate. */
export class Customer {
  constructor(
    public readonly id: Id,
    public readonly email: Email,
    public readonly status: CustomerStatus,
    public readonly createdAt: Timestamp,
  ) {}
}
