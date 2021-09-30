import { Injectable, OnDestroy } from '@angular/core';
import { Observable, timer, Subscription, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { switchMap, tap, share, retry, takeUntil } from 'rxjs/operators';

export type Currency = CurrencyInfo[];

export interface CurrencyInfo {
  D1: string
  H1: string
  H4: string
  M1: string
  M15: string
  M5: string
  id: number
  name: string
}

@Injectable({ providedIn : "root"})
export class HeroService implements OnDestroy {

  private allCurrencies$: Observable<CurrencyInfo[]>;

  private stopPolling = new Subject();

  constructor(private http: HttpClient) {
    this.allCurrencies$ = timer(1, 3000).pipe(
      switchMap(() => http.get<CurrencyInfo[]>('http://127.0.0.1:8050/ ')),
      retry(),
      tap(console.log),
      share(),
      takeUntil(this.stopPolling)
    );
  }


  getAllCurrencies(): Observable<CurrencyInfo[]> {
    return this.allCurrencies$.pipe(
      tap(() => console.log('data sent to subscriber'))
    );
  }

  ngOnDestroy() {
      this.stopPolling.next();
  }
}
