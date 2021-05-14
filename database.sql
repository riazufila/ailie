--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.2

-- Started on 2021-05-11 17:41:26 +08

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3066 (class 1262 OID 18731)
-- Name: ailie; Type: DATABASE; Schema: -; Owner: riazufila
--

CREATE DATABASE ailie WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';


ALTER DATABASE ailie OWNER TO riazufila;

\connect ailie

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 200 (class 1259 OID 18732)
-- Name: equipments; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.equipments (
    equip_id bigint NOT NULL,
    equip_name text NOT NULL,
    equip_star integer NOT NULL,
    equip_exclusive boolean NOT NULL,
    equip_pickup boolean DEFAULT false NOT NULL
);


ALTER TABLE public.equipments OWNER TO riazufila;

--
-- TOC entry 201 (class 1259 OID 18739)
-- Name: equipments_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.equipments_acquired (
    equip_acquired_id bigint NOT NULL,
    equip_id bigint NOT NULL,
    inventory_id bigint NOT NULL
);


ALTER TABLE public.equipments_acquired OWNER TO riazufila;

--
-- TOC entry 202 (class 1259 OID 18742)
-- Name: equipments_acquired_equip_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.equipments_acquired ALTER COLUMN equip_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipments_acquired_equip_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 203 (class 1259 OID 18744)
-- Name: equipments_equip_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.equipments ALTER COLUMN equip_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipments_equip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 204 (class 1259 OID 18746)
-- Name: guardians; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.guardians (
    guardian_id bigint NOT NULL,
    guardian_username text,
    guild_id bigint,
    guardian_position text,
    guardian_gems bigint DEFAULT 0 NOT NULL,
    guardian_trophy bigint DEFAULT 0 NOT NULL,
    guardian_summon_count integer DEFAULT 0 NOT NULL,
    guardian_gained_gems bigint DEFAULT 0 NOT NULL,
    guardian_gained_trophy bigint DEFAULT 0 NOT NULL,
    guardian_wins integer DEFAULT 0 NOT NULL,
    guardian_losses integer DEFAULT 0 NOT NULL,
    guardian_hourly timestamp with time zone,
    guardian_daily timestamp with time zone,
    guardian_daily_count integer DEFAULT 0 NOT NULL,
    guardian_exp bigint DEFAULT 0 NOT NULL,
    guardian_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_spent_gems bigint DEFAULT 0 NOT NULL,
    guardian_lose_trophy bigint DEFAULT 0 NOT NULL,
    guardian_won_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_won_gambled_count bigint DEFAULT 0 NOT NULL,
    guardian_lose_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_lose_gambled_count bigint DEFAULT 0 NOT NULL,
    guardian_gamble_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.guardians OWNER TO riazufila;

--
-- TOC entry 205 (class 1259 OID 18769)
-- Name: guilds; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.guilds (
    guild_id bigint NOT NULL,
    guild_name text NOT NULL
);


ALTER TABLE public.guilds OWNER TO riazufila;

--
-- TOC entry 206 (class 1259 OID 18775)
-- Name: heroes; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.heroes (
    hero_id bigint NOT NULL,
    hero_name text NOT NULL,
    hero_star integer NOT NULL,
    hero_pickup boolean DEFAULT false NOT NULL,
    equip_id bigint,
    hero_stats json,
    hero_buffs json,
    hero_skill json,
    hero_triggers json
);


ALTER TABLE public.heroes OWNER TO riazufila;

--
-- TOC entry 207 (class 1259 OID 18782)
-- Name: heroes_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.heroes_acquired (
    hero_acquired_id bigint NOT NULL,
    hero_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    hero_acquired_exp bigint DEFAULT 0 NOT NULL,
    hero_acquired_limit_break integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.heroes_acquired OWNER TO riazufila;

--
-- TOC entry 208 (class 1259 OID 18787)
-- Name: heroes_acquired_hero_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.heroes_acquired ALTER COLUMN hero_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.heroes_acquired_hero_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 209 (class 1259 OID 18789)
-- Name: heroes_hero_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.heroes ALTER COLUMN hero_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.heroes_hero_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 210 (class 1259 OID 18791)
-- Name: inventories; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.inventories (
    inventory_id bigint NOT NULL,
    guardian_id bigint NOT NULL
);


ALTER TABLE public.inventories OWNER TO riazufila;

--
-- TOC entry 211 (class 1259 OID 18794)
-- Name: inventories_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.inventories ALTER COLUMN inventory_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.inventories_inventory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 2913 (class 2606 OID 18797)
-- Name: equipments_acquired equipments_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT equipments_acquired_pkey PRIMARY KEY (equip_acquired_id);


--
-- TOC entry 2911 (class 2606 OID 18799)
-- Name: equipments equipments_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments
    ADD CONSTRAINT equipments_pkey PRIMARY KEY (equip_id);


--
-- TOC entry 2915 (class 2606 OID 18801)
-- Name: guardians guardians_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guardians
    ADD CONSTRAINT guardians_pkey PRIMARY KEY (guardian_id);


--
-- TOC entry 2917 (class 2606 OID 18803)
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 2921 (class 2606 OID 18805)
-- Name: heroes_acquired heroes_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT heroes_acquired_pkey PRIMARY KEY (hero_acquired_id);


--
-- TOC entry 2919 (class 2606 OID 18807)
-- Name: heroes heroes_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes
    ADD CONSTRAINT heroes_pkey PRIMARY KEY (hero_id);


--
-- TOC entry 2923 (class 2606 OID 18809)
-- Name: inventories inventories_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_pkey PRIMARY KEY (inventory_id);


--
-- TOC entry 2924 (class 2606 OID 18810)
-- Name: equipments_acquired equipments_equip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT equipments_equip_id_fkey FOREIGN KEY (equip_id) REFERENCES public.equipments(equip_id);


--
-- TOC entry 2927 (class 2606 OID 18815)
-- Name: heroes equipments_equip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes
    ADD CONSTRAINT equipments_equip_id_fkey FOREIGN KEY (equip_id) REFERENCES public.equipments(equip_id) NOT VALID;


--
-- TOC entry 2930 (class 2606 OID 18820)
-- Name: inventories guardians_guardian_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT guardians_guardian_id_fkey FOREIGN KEY (guardian_id) REFERENCES public.guardians(guardian_id) NOT VALID;


--
-- TOC entry 2926 (class 2606 OID 18825)
-- Name: guardians guilds_guild_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guardians
    ADD CONSTRAINT guilds_guild_id_fkey FOREIGN KEY (guild_id) REFERENCES public.guilds(guild_id) NOT VALID;


--
-- TOC entry 2928 (class 2606 OID 18830)
-- Name: heroes_acquired heroes_hero_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT heroes_hero_id_fkey FOREIGN KEY (hero_id) REFERENCES public.heroes(hero_id);


--
-- TOC entry 2929 (class 2606 OID 18835)
-- Name: heroes_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- TOC entry 2925 (class 2606 OID 18840)
-- Name: equipments_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


-- Completed on 2021-05-11 17:41:27 +08

--
-- PostgreSQL database dump complete
--

