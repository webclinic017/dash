import { Component, OnInit } from '@angular/core';
import { ses } from '../hero';
import {HttpClient , HttpHeaders, HttpClientModule} from '@angular/common/http';

import { Injectable, OnDestroy } from '@angular/core';
import { Observable, timer, Subscription, Subject } from 'rxjs';

import { switchMap, tap, share, retry, takeUntil } from 'rxjs/operators';

import { EngService , CurrencyInfo_eng} from './eng.service';

type ost = OstInfo[];

interface OstInfo {
  c: string
  t: string
}


@Component({
  selector: 'app-eng',
  templateUrl: './eng.component.html',
  styleUrls: ['./eng.component.css']
})

export class EngComponent implements OnInit {



  currencyInfo_eng$: Observable<CurrencyInfo_eng[]>;

  postId : any;

     addPersone(e : string, a : string){

    this.http.post<any>('http://127.0.0.1:8050/eng' , {"curr" : e , "tf" : a }  ).subscribe(data => {
        this.postId = data.aa;
    })

    console.log(this.postId)

    }

  constructor( private service : EngService , private http: HttpClient  ) {

    this.currencyInfo_eng$ = service.getAllCurrencies_eng();

   }

  ngOnInit(): void {


  }


}

