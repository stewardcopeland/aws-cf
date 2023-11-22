/************************************************************************************
    Scrub history of Full Loads. 
    Recreate table to instead represents what we would have if the pipeline was running as incremental loads.
*************************************************************************************/


with RECURSIVE current_layer (
        layer_ID, 
        seqn, 
        UNIT,
        LOC,
        STARTDATE ,
        LAG ,
        BASEFCST ,
        TOTFCST ,
        BATCH_RUN_ID,
        LOAD_DT_TS,
        CHG_OP
        
    ) AS (
        -- Anchor Clause            
        SELECT 
            1 as layer_ID , 
            t2.seqn as seqn ,
//            L1.item as sort_key , -- keep for debugging
            L1.UNIT ,
            L1.LOC ,
            L1.STARTDATE ,
            L1.LAG ,
            L1.BASEFCST ,
            L1.TOTFCST ,
            L1.BATCH_RUN_ID ,
            L1.LOAD_DT_TS,
            'INSERT' AS CHG_OP
        FROM FCST L1
            
        INNER JOIN (
          select batch_run_id , row_number() over(order by batch_run_id) seqn 
              from (
                  select distinct batch_run_id
                  from FCST
                  order by batch_run_id
              )
        ) T2 ON L1.batch_run_id = T2.batch_run_id and t2.seqn = 1
        where L1.LOC in ('104262'          )
        UNION ALL
        -- Recursive Clause
        SELECT 
            layer_ID + 1 as layer_ID ,
            t2.seqn , 
//            sort_key || '->' || nxt_layer.item,
            nxt_layer.UNIT,
            nxt_layer.LOC,
            nxt_layer.STARTDATE ,
            nxt_layer.LAG ,
            nxt_layer.BASEFCST ,
            nxt_layer.TOTFCST ,
            nxt_layer.BATCH_RUN_ID,
            nxt_layer.LOAD_DT_TS,
            CASE WHEN nxt_layer.BASEFCST <> current_layer.BASEFCST then 'UPDATE' else NULL end as  CHG_OP -- Compare sequential values, Record a change in this field
        FROM current_layer 
        INNER JOIN ( -- increment batch_run_id. Use this to isolate next layer to only be records from NEXT batch_run_id
            select batch_run_id , row_number() over(order by batch_run_id) seqn 
            from (
                select distinct batch_run_id
                from FCST
                order by batch_run_id
            )
        ) T2 ON (current_layer.seqn + 1) = T2.seqn
  
        INNER JOIN FCSTPERFSTATIC nxt_layer 
            ON current_layer.UNIT = nxt_layer.UNIT
            AND current_layer.LOC = nxt_layer.LOC
            AND current_layer.STARTDATE = nxt_layer.STARTDATE
            AND current_layer.LAG = nxt_layer.LAG
            AND T2.batch_run_id = nxt_layer.batch_run_id
    )
    
    SELECT *
    from current_layer
    where CHG_OP IS NOT NULL -- Only keep initial records 'INSERT', and subsequent records that have some changes 'UPDATE'
    order by batch_run_id
;