
import { Component, Input, VERSION ,OnInit} from '@angular/core';
import { MockServerService } from './ser.service';
import { Stock } from './ser.service';
import {
  ColDef,
  ColumnApi,
  GetRowNodeIdFunc,
  GridApi,
  GridReadyEvent,
  ValueGetterParams
} from 'ag-grid-community';
import { Observable } from 'rxjs';
import { formatCurrency } from '@angular/common';



@Component({
  selector: 'app-ser',
  templateUrl: './ser.component.html',
  styleUrls: ['./ser.component.css'],
  providers: [MockServerService]
})
export class SerComponent implements OnInit {



  public rowData$: Observable<Stock[]>;
  public selectedCurrency: string = 'USD';

  public defaultColDef: ColDef;
  public getRowNodeId: GetRowNodeIdFunc;
  public frameworkComponents: any;
  public columnTypes: { [key: string]: ColDef };
  public immutableData: boolean;


  constructor(private mockServerService: MockServerService) {

    this.defaultColDef = {
      flex: 1,
      minWidth: 100,
      resizable: true
    };
    this.immutableData = true;
    this.getRowNodeId = (data: any): string => data.id;
    this.columnTypes = {


    };

    this.rowData$ = this.mockServerService.getDataObservable();

    }

  ngOnInit(): void {

  console.log(this.rowData$);


  }

}
