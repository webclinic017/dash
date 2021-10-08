import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ColDef } from 'ag-grid-community';



export interface Stock {
  D1: string
  H1: string
  H4: string
  M1: string
  M15: string
  M5: string
  id: number
  name: string
}


@Injectable()
export class MockServerService {
  private stocksUrl: string = 'http://127.0.0.1:8050/';


  immutableData: Stock[] ;

  constructor(private http: HttpClient) {
  this.immutableData = []
  }

  getDataObservable(): Observable<Stock[]> {
    return new Observable<Stock[]>(observer => {
      this.http.get<Stock[]>(this.stocksUrl).subscribe((data: Stock[]) => {
        this.immutableData = data;
        observer.next(this.immutableData);

        //setInterval(() => {
        //  this.immutableData = this.immutableData.map((row: Stock) =>
        //    this.updateRandomRowWithData(row)
        //  );

        //  observer.next(this.immutableData);
        //}, 1000);
      });
    });
  }

 }
