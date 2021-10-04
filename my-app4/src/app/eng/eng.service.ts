import { Injectable, OnDestroy } from '@angular/core';
import { Observable, timer, Subscription, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { switchMap, tap, share, retry, takeUntil } from 'rxjs/operators';

export type Currency_eng = CurrencyInfo_eng[];

export interface CurrencyInfo_eng {
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
export class EngService implements OnDestroy {

  private allCurrencies_eng$: Observable<CurrencyInfo_eng[]>;

  private stopPolling_eng = new Subject();

  constructor(private http: HttpClient) {
    this.allCurrencies_eng$ = timer(1, 3000).pipe(
      switchMap(() => http.get<CurrencyInfo_eng[]>('http://127.0.0.1:8050/eng ')),
      retry(),
      tap(console.log),
      share(),
      takeUntil(this.stopPolling_eng)
    );

  }


  getAllCurrencies_eng(): Observable<CurrencyInfo_eng[]> {
    return this.allCurrencies_eng$.pipe(
      tap(() => console.log('data sent to subscriber'))
    );
  }


  ngOnDestroy() {
      this.stopPolling_eng.next();
  }
}
