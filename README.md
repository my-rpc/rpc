# rpc

-- Below code is used to create a procedure and an Event which will be executed every day at 8:30 am

-- first we need to activate global event scheduler 

    SHOW PROCESSLIST;  # show active process
    SET GLOBAL event_scheduler = OFF;   # inactive state
    SET GLOBAL event_scheduler = ON;   # Active state

    SHOW EVENTS; # show all events.


    DROP PROCEDURE IF EXISTS contractStatusUpdatePro;
    DELIMITER //
    CREATE PROCEDURE contractStatusUpdatePro()
    BEGIN
    update position_history SET status = 0 WHERE  DATE_ADD(end_date, INTERVAL 5 DAY) < CURRENT_DATE AND status = 1;
    End;
    //
    DELIMITER ;


    DROP EVENT IF EXISTS updateContractStatusEv
    DELIMITER //
    CREATE EVENT updateContractStatusEv
        ON SCHEDULE EVERY 1 DAY
        STARTS "2021-10-14 8:30:00"
        DO CALL contractStatusUpdatePro;
    //
    DELIMITER ;

    